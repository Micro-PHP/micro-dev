<?php

declare(strict_types=1);

namespace Micro\Framework\DependencyInjection\Definition;

readonly class FactoryDefinition
{
    public function __construct(
        public string $id,
        public \Closure $factory
    ) {
    }
}
