<?php

declare(strict_types=1);

namespace Micro\Framework\DependencyInjection\Tests\Unit;

readonly class NamedServiceDecorator implements NamedInterface
{
    public function __construct(
        private object $decorated,
        private string $name
    ) {
    }

    public function getName(): string
    {
        return $this->decorated->getName() . $this->name;
    }
}