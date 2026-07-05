<?php

declare(strict_types=1);

namespace Micro\Framework\DependencyInjection\Builder;

use Micro\Framework\DependencyInjection\Definition\DecoratorDefinition;
use Micro\Framework\DependencyInjection\Definition\FactoryDefinition;
use Micro\Framework\DependencyInjection\Definition\ServiceDefinition;
use Micro\Framework\DependencyInjection\MutableContainerInterface;

interface ContainerBuilderInterface
{
    public function service(ServiceDefinition $definition): static;

    public function factory(FactoryDefinition $definition): static;

    public function decorator(DecoratorDefinition $definition): static;

    public function build(): MutableContainerInterface;
}
