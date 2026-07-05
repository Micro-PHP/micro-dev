<?php

declare(strict_types=1);

/*
 *  This file is part of the Micro framework package.
 *
 *  (c) Stanislau Komar <kost@micro-php.net>
 *
 *  For the full copyright and license information, please view the LICENSE
 *  file that was distributed with this source code.
 */

namespace Micro\Framework\BootPluginDependent\Tests\Unit\Boot;

use Micro\Framework\DependencyInjection\Container;
use Micro\Framework\BootPluginDependent\Boot\DependedPluginsBootLoader;
use Micro\Framework\Kernel\Kernel;
use Micro\Framework\Kernel\KernelInterface;
use Micro\Framework\BootPluginDependent\Plugin\PluginDependedInterface;
use Micro\Framework\BootPluginDependent\Tests\Unit\EmptyPlugin;
use Micro\Framework\BootPluginDependent\Tests\Unit\PluginHasDepends;
use Micro\Framework\BootPluginDependent\Tests\Unit\PluginHasEmptyDepends;
use PHPUnit\Framework\TestCase;

class DependedPluginsBootLoaderTest extends TestCase
{
    private KernelInterface|null $kernel = null;

    private object $pluginNotHasDepends;

    private PluginDependedInterface $pluginDependedWithEmptyDepends;

    private PluginDependedInterface $pluginDependedWithDepends;

    protected function setUp(): void
    {
    }

    public function testBoot(): void
    {
        $container = new Container();
        foreach ([PluginHasDepends::class, EmptyPlugin::class, PluginHasEmptyDepends::class] as $pluginClass) {
            $container->register(
                $pluginClass,
                static fn (): object => new $pluginClass()
            );
        }

        $this->kernel = new Kernel(
            [
                PluginHasDepends::class,
            ],
            [],
            $container,
        );

        $bootLoader = new DependedPluginsBootLoader($this->kernel);
        $this->kernel->addBootLoader($bootLoader);
        $this->kernel->run();

        $i = 0;
        foreach ($this->kernel->plugins() as $plugin) {
            ++$i;
        }

        $this->assertEquals(3, $i);
    }
}
