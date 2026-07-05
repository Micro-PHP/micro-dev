<?php

/*
 *  This file is part of the Micro framework package.
 *
 *  (c) Stanislau Komar <kost@micro-php.net>
 *
 *  For the full copyright and license information, please view the LICENSE
 *  file that was distributed with this source code.
 */

namespace Micro\Framework\BootDependency\Tests\Unit\Boot;

use Micro\Framework\DependencyInjection\Container;
use Micro\Framework\Autowire\ContainerAutowire;
use Micro\Framework\BootDependency\Boot\DependencyProviderBootLoader;
use Micro\Framework\BootDependency\Plugin\DependencyProviderInterface;
use Micro\Framework\DependencyInjection\MutableContainerInterface;
use PHPUnit\Framework\TestCase;

class DependencyProviderBootLoaderTest extends TestCase
{
    public function testBoot(): void
    {
        $container = new Container();

        $dataProviderBootLoader = new DependencyProviderBootLoader($container);

        $pluginMock = $this->createMock(DependencyProviderInterface::class);
        $pluginMock
            ->expects($this->once())
            ->method('provideDependencies');

        $pluginNotDependencyProvider = new class() {
            public function provideDependencies()
            {
                throw new \LogicException('Should not be executed!');
            }
        };

        foreach ([$pluginMock, $pluginNotDependencyProvider] as $plugin) {
            $dataProviderBootLoader->boot($plugin);
        }
    }

    public function testProvidesAutowiringContainerThroughMutableContract(): void
    {
        $bootLoader = new DependencyProviderBootLoader(new Container());
        $plugin = new class() implements DependencyProviderInterface {
            public ?MutableContainerInterface $container = null;

            public function provideDependencies(MutableContainerInterface $container): void
            {
                $this->container = $container;
            }
        };

        $bootLoader->boot($plugin);

        self::assertInstanceOf(ContainerAutowire::class, $plugin->container);
    }
}
