<?php

declare(strict_types=1);

namespace Micro\Framework\DependencyInjection\Builder;

use Micro\Framework\DependencyInjection\Container;
use Micro\Framework\DependencyInjection\Definition\DecoratorDefinition;
use Micro\Framework\DependencyInjection\Definition\FactoryDefinition;
use Micro\Framework\DependencyInjection\Definition\ServiceDefinition;
use Micro\Framework\DependencyInjection\MutableContainerInterface;

class ContainerBuilder implements ContainerBuilderInterface
{
    /** @var array<string, ServiceDefinition> */
    private array $services = [];

    /** @var array<string, FactoryDefinition> */
    private array $factories = [];

    /** @var list<DecoratorDefinition> */
    private array $decorators = [];

    public function service(ServiceDefinition $definition): static
    {
        $this->services[$definition->id] = $definition;

        return $this;
    }

    public function factory(FactoryDefinition $definition): static
    {
        $this->factories[$definition->id] = $definition;

        return $this;
    }

    public function decorator(DecoratorDefinition $definition): static
    {
        $this->decorators[] = $definition;

        return $this;
    }

    public function build(): MutableContainerInterface
    {
        $container = new Container();

        foreach ($this->services as $definition) {
            $container->set($definition->id, $definition->service);
        }

        foreach ($this->factories as $definition) {
            $container->register($definition->id, $definition->factory);
        }

        foreach ($this->decorators as $definition) {
            $container->decorate(
                $definition->id,
                $definition->decorator,
                $definition->priority
            );
        }

        return $container;
    }
}
