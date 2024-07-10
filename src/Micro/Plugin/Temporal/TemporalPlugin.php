<?php

namespace Micro\Plugin\Temporal;

use Micro\Component\DependencyInjection\Autowire\AutowireHelperFactory;
use Micro\Component\DependencyInjection\Autowire\AutowireHelperFactoryInterface;
use Micro\Framework\DependencyInjection\Container;
use Micro\Framework\BootConfiguration\Plugin\ConfigurableInterface;
use Micro\Framework\BootDependency\Plugin\DependencyProviderInterface;
use Micro\Framework\BootConfiguration\Plugin\PluginConfigurationTrait;
use Micro\Library\DTO\SerializerFacadeInterface;
use Micro\Plugin\Locator\Facade\LocatorFacadeInterface;
use Micro\Plugin\Temporal\Activity\Factory\ActivityStubFactory;
use Micro\Plugin\Temporal\Activity\Factory\ActivityStubFactoryInterface;
use Micro\Plugin\Temporal\Configuration\TemporalPluginConfigurationInterface;
use Micro\Plugin\Temporal\Facade\TemporalFacade;
use Micro\Plugin\Temporal\Facade\TemporalFacadeInterface;
use Micro\Plugin\Temporal\RoadRunner\Expander\Environment\EnvironmentExpanderFactory;
use Micro\Plugin\Temporal\RoadRunner\Expander\Environment\EnvironmentExpanderFactoryInterface;
use Micro\Plugin\Temporal\Worker\Expander\WorkerExpanderFactory;
use Micro\Plugin\Temporal\Worker\Expander\WorkerExpanderFactoryInterface;
use Micro\Plugin\Temporal\Worker\Factory\WorkerFactory;
use Micro\Plugin\Temporal\Worker\Factory\WorkerFactoryInterface;
use Micro\Plugin\Temporal\Workflow\Client\Factory\ClientFactory;
use Micro\Plugin\Temporal\Workflow\Client\Factory\ClientFactoryInterface;
use Micro\Plugin\Temporal\Workflow\Client\Repository\ClientRepositoryFactory;
use Micro\Plugin\Temporal\Workflow\Client\Repository\ClientRepositoryFactoryInterface;
use Micro\Plugin\Temporal\Workflow\Client\Repository\ClientRepositoryInterface;
use Micro\Plugin\Temporal\Workflow\DataConverter\DataConverterFactory;
use Micro\Plugin\Temporal\Workflow\DataConverter\DataConverterFactoryInterface;

/**
 * @method TemporalPluginConfigurationInterface configuration()
 */
class TemporalPlugin implements DependencyProviderInterface, ConfigurableInterface
{
    use PluginConfigurationTrait;

    /**
     * @var SerializerFacadeInterface|null
     */
    private ?SerializerFacadeInterface $serializerFacade = null;

    /**
     * @var LocatorFacadeInterface|null
     */
    private ?LocatorFacadeInterface $locatorFacade = null;

    /**
     * @var AutowireHelperFactoryInterface|null
     */
    private ?AutowireHelperFactoryInterface $autowireHelperFactory = null;

    /**
     * {@inheritDoc}
     */
    public function provideDependencies(Container $container): void
    {
        $container->register(TemporalFacadeInterface::class, function (
            SerializerFacadeInterface $serializerFacade,
            LocatorFacadeInterface $locatorFacade
        ) use($container) {
            $this->serializerFacade = $serializerFacade;
            $this->locatorFacade = $locatorFacade;
            $this->autowireHelperFactory = new AutowireHelperFactory($container);

            return $this->createFacade();
        });
    }

    /**
     * @return TemporalFacadeInterface
     */
    protected function createFacade(): TemporalFacadeInterface
    {
        return new TemporalFacade(
            clientRepository: $this->createWorkflowClientRepository(),
            workerFactory: $this->createWorkerFactory(),
            activityStubFactory: $this->createActivityStubFactory()
        );
    }

    /**
     * @return ClientFactoryInterface
     */
    protected function createWorkflowClientFactory(): ClientFactoryInterface
    {
        return new ClientFactory($this->createDataConverterFactory());
    }

    /**
     * @return DataConverterFactoryInterface
     */
    protected function createDataConverterFactory(): DataConverterFactoryInterface
    {
        return new DataConverterFactory($this->serializerFacade);
    }

    /**
     * @return ClientRepositoryFactoryInterface
     */
    protected function createWorkflowClientRepositoryFactory(): ClientRepositoryFactoryInterface
    {
        return new ClientRepositoryFactory(
            clientFactory: $this->createWorkflowClientFactory(),
            pluginConfiguration: $this->configuration()
        );
    }

    /**
     * @return ClientRepositoryInterface
     */
    protected function createWorkflowClientRepository(): ClientRepositoryInterface
    {
        return $this->createWorkflowClientRepositoryFactory()->create();
    }

    protected function createWorkerExpanderFactory(): WorkerExpanderFactoryInterface
    {
        return new WorkerExpanderFactory(
            $this->locatorFacade,
            $this->autowireHelperFactory
        );
    }

    /**
     * @return ActivityStubFactoryInterface
     */
    protected function createActivityStubFactory(): ActivityStubFactoryInterface
    {
        return new ActivityStubFactory();
    }

    /**
     * @return WorkerFactoryInterface
     */
    protected function createWorkerFactory(): WorkerFactoryInterface
    {
        return new WorkerFactory(
            $this->createWorkerExpanderFactory(),
            $this->createDataConverterFactory(),
            $this->createRREnvironmentExpanderFactory(),
            $this->configuration()
        );
    }

    /**
     * @return EnvironmentExpanderFactoryInterface
     */
    protected function createRREnvironmentExpanderFactory(): EnvironmentExpanderFactoryInterface
    {
        return new EnvironmentExpanderFactory($this->configuration());
    }
}