<?php

declare(strict_types=1);

namespace Micro\Framework\DependencyInjection\Definition;

readonly class DecoratorDefinition
{
    public function __construct(
        public string $id,
        public \Closure $decorator,
        public int $priority = 0
    ) {
    }
}
