<?php

/*
 *  This file is part of the Micro framework package.
 *
 *  (c) Stanislau Komar <kost@micro-php.net>
 *
 *  For the full copyright and license information, please view the LICENSE
 *  file that was distributed with this source code.
 */

namespace Micro\Framework\KernelApp;

use Micro\Framework\Autowire\Builder\AutowireContainerBuilder;
use Micro\Framework\Autowire\Builder\AutowireContainerBuilderInterface;
use Micro\Framework\Autowire\Definition\AutowiredClassDefinition;
use Micro\Framework\DependencyInjection\MutableContainerInterface;
use Micro\Framework\BootConfiguration\Boot\ConfigurationProviderBootLoader;
use Micro\Framework\BootPluginDependent\Boot\DependedPluginsBootLoader;
use Micro\Framework\BootDependency\Boot\DependencyProviderBootLoader;
use Micro\Framework\BootConfiguration\Configuration\ApplicationConfigurationInterface;
use Micro\Framework\Kernel\KernelBuilder;
use Micro\Framework\Kernel\KernelInterface;
use Micro\Framework\Kernel\Plugin\PluginBootLoaderInterface;
use Micro\Framework\KernelApp\Business\KernelActionProcessorInterface;
use Micro\Framework\KernelApp\Business\KernelRunActionProcessor;
use Micro\Framework\KernelApp\Business\KernelTerminateActionProcessor;
use Micro\Plugin\EventEmitter\EventEmitterPlugin;
use Micro\Plugin\Locator\LocatorPlugin;

class AppKernel implements AppKernelInterface
{
    private bool $isTerminated;

    private bool $isStarted;

    private ?KernelInterface $kernel;

    /**
     * @var PluginBootLoaderInterface[]
     */
    private array $additionalBootLoaders = [];

    /**
     * @param ApplicationConfigurationInterface|array<string, string> $configuration
     * @param class-string[]                                          $plugins
     */
    public function __construct(
        private readonly ApplicationConfigurationInterface|array $configuration = [],
        private array $plugins = [],
        private readonly string $environment = 'dev'
    ) {
        $this->kernel = null;
        $this->isTerminated = false;
        $this->isStarted = false;
    }

    /**
     * {@inheritDoc}
     */
    public function container(): MutableContainerInterface
    {
        return $this->kernel()->container();
    }

    /**
     * {@inheritDoc}
     */
    public function plugins(?string $pluginInterface = null): \Traversable
    {
        return $this->kernel()->plugins($pluginInterface);
    }

    /**
     * {@inheritDoc}
     */
    public function run(): void
    {
        if ($this->isStarted) {
            return;
        }

        $this->kernel = $this->createKernel();

        $this->kernel->run();

        $this->createInitActionProcessor()->process($this);

        $this->isStarted = true;
    }

    /**
     * {@inheritDoc}
     */
    public function terminate(): void
    {
        if ($this->isTerminated || !$this->isStarted) {
            return;
        }

        $this->createTerminateActionProcessor()->process($this);

        $this->isTerminated = true;
    }

    /**
     * {@inheritDoc}
     */
    public function environment(): string
    {
        return $this->environment;
    }

    /**
     * {@inheritDoc}
     */
    public function isDevMode(): bool
    {
        return str_starts_with($this->environment(), 'dev');
    }

    /**
     * {@inheritDoc}
     */
    public function addBootLoader(PluginBootLoaderInterface $bootLoader): self
    {
        $this->additionalBootLoaders[] = $bootLoader;

        return $this;
    }

    /**
     * {@inheritDoc}
     */
    public function loadPlugin(string $pluginClass): void
    {
        $this->kernel()->loadPlugin($pluginClass);
    }

    protected function createKernel(): KernelInterface
    {
        $plugins = array_unique([
            EventEmitterPlugin::class,
            LocatorPlugin::class,
            ...$this->plugins,
        ]);
        $this->plugins = [];

        $containerBuilder = $this->createContainerBuilder();
        foreach ($plugins as $pluginClass) {
            $containerBuilder->autowiredClass(new AutowiredClassDefinition(
                id: $pluginClass,
                class: $pluginClass
            ));
        }
        $container = $containerBuilder->build();

        return $this
            ->createKernelBuilder()
            ->setContainer($container)
            ->addBootLoaders($this->createBootLoaderCollection($container))
            ->setApplicationPlugins($plugins)
            ->build();
    }

    protected function kernel(): KernelInterface
    {
        if (!$this->kernel) {
            $trace = debug_backtrace();
            $caller = $trace[1];
            /**
             * @var string $cc
             *
             * @phpstan-ignore-next-line
             *
             * @psalm-suppress PossiblyUndefinedArrayOffset
             */
            $cc = $caller['class'];
            $cm = $caller['function'];

            throw new \RuntimeException(sprintf('Method %s::%s can not be called before %s::run() execution.', $cc, $cm, KernelInterface::class));
        }

        return $this->kernel;
    }

    protected function createKernelBuilder(): KernelBuilder
    {
        return new KernelBuilder();
    }

    protected function createContainerBuilder(): AutowireContainerBuilderInterface
    {
        return new AutowireContainerBuilder();
    }

    protected function createInitActionProcessor(): KernelActionProcessorInterface
    {
        return new KernelRunActionProcessor();
    }

    protected function createTerminateActionProcessor(): KernelActionProcessorInterface
    {
        return new KernelTerminateActionProcessor();
    }

    /**
     * @return PluginBootLoaderInterface[]
     */
    protected function createBootLoaderCollection(MutableContainerInterface $container): array
    {
        $bootLoaders = $this->additionalBootLoaders;

        $this->additionalBootLoaders = [];

        return [
            new ConfigurationProviderBootLoader($this->configuration),
            new DependencyProviderBootLoader($container),
            new DependedPluginsBootLoader($this),
            ...$bootLoaders,
        ];
    }

    public function setBootLoaders(iterable $bootLoaders): KernelInterface
    {
        $this->kernel()->setBootLoaders($bootLoaders);

        return $this;
    }
}
