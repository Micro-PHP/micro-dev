<?php

declare(strict_types=1);

namespace Micro\Framework\DependencyInjection\Tests\Unit;

readonly class NamedService implements NamedInterface
{
    public function __construct(private string $name)
    {
    }

    public function getName(): string
    {
        return $this->name;
    }
}