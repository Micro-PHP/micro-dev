<?php

/*
 *  This file is part of the Micro framework package.
 *
 *  (c) Stanislau Komar <kost@micro-php.net>
 *
 *  For the full copyright and license information, please view the LICENSE
 *  file that was distributed with this source code.
 */

namespace Micro\Plugin\Locator;

use Micro\Framework\DependencyInjection\MutableContainerInterface;
use Micro\Framework\BootDependency\Plugin\DependencyProviderInterface;
use Micro\Framework\Kernel\Plugin\PluginCollectionInterface;
use Micro\Plugin\Locator\Facade\LocatorFacade;
use Micro\Plugin\Locator\Facade\LocatorFacadeInterface;
use Micro\Plugin\Locator\Locator\LocatorFactory;
use Micro\Plugin\Locator\Locator\LocatorFactoryInterface;

class LocatorPlugin implements DependencyProviderInterface
{
    public function provideDependencies(MutableContainerInterface $container): void
    {
        $container->register(LocatorFacadeInterface::class, function (
            PluginCollectionInterface $pluginCollection
        ) {
            return $this->createLocatorFacade($pluginCollection);
        });
    }

    protected function createLocatorFacade(
        PluginCollectionInterface $pluginCollection
    ): LocatorFacadeInterface {
        return new LocatorFacade(
            $this->createLocatorFactory($pluginCollection)
        );
    }

    protected function createLocatorFactory(
        PluginCollectionInterface $pluginCollection
    ): LocatorFactoryInterface {
        return new LocatorFactory($pluginCollection);
    }
}
