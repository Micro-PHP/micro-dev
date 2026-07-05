<?php

declare(strict_types=1);

namespace Micro\Framework\Kernel\Tests\Unit;

use Micro\Framework\Kernel\Plugin\PluginRegistry;
use PHPUnit\Framework\TestCase;

class PluginRegistryTest extends TestCase
{
    public function testProvidesLoadedPluginsAndFiltersByType(): void
    {
        $registry = new PluginRegistry();
        $matching = new \ArrayObject();
        $registry->add('matching', $matching);
        $registry->add('other', new \stdClass());

        self::assertTrue($registry->has('matching'));
        self::assertSame(
            [$matching],
            iterator_to_array($registry->plugins(\ArrayAccess::class), false)
        );
        self::assertCount(2, iterator_to_array($registry->plugins(), false));
    }
}
