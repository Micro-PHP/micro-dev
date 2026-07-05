<?php

declare(strict_types=1);

namespace Micro\Framework\Autowire\Builder;

use Micro\Framework\Autowire\AutowireHelper;
use Micro\Framework\Autowire\ContainerAutowire;
use Micro\Framework\Autowire\Definition\AutowiredClassDefinition;
use Micro\Framework\DependencyInjection\Builder\ContainerBuilder;
use Micro\Framework\DependencyInjection\Builder\ContainerBuilderInterface;
use Micro\Framework\DependencyInjection\Definition\DecoratorDefinition;
use Micro\Framework\DependencyInjection\Definition\FactoryDefinition;
use Micro\Framework\DependencyInjection\Definition\ServiceDefinition;
use Micro\Framework\DependencyInjection\MutableContainerInterface;
use Psr\Container\ContainerInterface;

readonly class AutowireContainerBuilder implements AutowireContainerBuilderInterface
{
    public function __construct(
        private ContainerBuilderInterface $containerBuilder = new ContainerBuilder()
    ) {
    }

    public function service(ServiceDefinition $definition): static
    {
        $this->containerBuilder->service($definition);

        return $this;
    }

    public function factory(FactoryDefinition $definition): static
    {
        $this->containerBuilder->factory($definition);

        return $this;
    }

    public function decorator(DecoratorDefinition $definition): static
    {
        $this->containerBuilder->decorator($definition);

        return $this;
    }

    public function autowiredClass(AutowiredClassDefinition $definition): static
    {
        $this->factory(new FactoryDefinition(
            $definition->id,
            static function (ContainerInterface $container) use ($definition): object {
                $factory = (new AutowireHelper($container))->autowire($definition->class);

                return $factory();
            }
        ));

        return $this;
    }

    public function build(): MutableContainerInterface
    {
        $container = $this->containerBuilder->build();

        return $container instanceof ContainerAutowire
            ? $container
            : new ContainerAutowire($container);
    }
}
