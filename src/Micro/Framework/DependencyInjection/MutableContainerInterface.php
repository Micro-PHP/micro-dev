<?php

declare(strict_types=1);

namespace Micro\Framework\DependencyInjection;

use Psr\Container\ContainerInterface;

interface MutableContainerInterface extends
    ContainerInterface,
    ContainerRegistryInterface,
    ContainerDecoratorInterface
{
}
