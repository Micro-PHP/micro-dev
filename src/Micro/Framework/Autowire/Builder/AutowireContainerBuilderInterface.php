<?php

declare(strict_types=1);

namespace Micro\Framework\Autowire\Builder;

use Micro\Framework\Autowire\Definition\AutowiredClassDefinition;
use Micro\Framework\DependencyInjection\Builder\ContainerBuilderInterface;

interface AutowireContainerBuilderInterface extends ContainerBuilderInterface
{
    public function autowiredClass(AutowiredClassDefinition $definition): static;
}
