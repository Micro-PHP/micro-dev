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

namespace Micro\Plugin\Logger\Tests\Unit;

use Micro\Framework\Autowire\ContainerAutowire;
use Micro\Framework\DependencyInjection\Container;
use Micro\Framework\Kernel\Plugin\PluginCollectionInterface;
use Micro\Plugin\Logger\Facade\LoggerFacadeInterface;
use Micro\Plugin\Logger\LoggerPlugin;
use Micro\Plugin\Logger\LoggerPluginConfiguration;
use PHPUnit\Framework\TestCase;

/**
 * @author GTPChat
 */
class LoggerPluginTest extends TestCase
{
    public function testProvideDependencies(): void
    {
        $kernelMock = $this->createMock(PluginCollectionInterface::class);
        $container = new ContainerAutowire(new Container());
        $container->register(PluginCollectionInterface::class, fn () => $kernelMock);

        $configMock = $this->createMock(LoggerPluginConfiguration::class);

        $loggerPlugin = new LoggerPlugin();
        $loggerPlugin->setConfiguration($configMock);
        $loggerPlugin->provideDependencies($container);

        $this->assertTrue($container->has(LoggerFacadeInterface::class));
        $loggerFacade = $container->get(LoggerFacadeInterface::class);
        $this->assertInstanceOf(LoggerFacadeInterface::class, $loggerFacade);
    }
}
