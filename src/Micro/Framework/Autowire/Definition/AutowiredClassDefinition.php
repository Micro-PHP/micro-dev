<?php

declare(strict_types=1);

namespace Micro\Framework\Autowire\Definition;

readonly class AutowiredClassDefinition
{
    /**
     * @param class-string $class
     */
    public function __construct(
        public string $id,
        public string $class
    ) {
    }
}
