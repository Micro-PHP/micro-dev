<?php

declare(strict_types=1);

namespace Micro\Framework\DependencyInjection\Definition;

readonly class ServiceDefinition
{
    public function __construct(
        public string $id,
        public object $service
    ) {
    }
}
