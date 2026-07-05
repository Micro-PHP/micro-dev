<?php

/*
 *  This file is part of the Micro framework package.
 *
 *  (c) Stanislau Komar <kost@micro-php.net>
 *
 *  For the full copyright and license information, please view the LICENSE
 *  file that was distributed with this source code.
 */

namespace Micro\Plugin\ConfigurationHelper;

use Micro\Framework\DependencyInjection\MutableContainerInterface;
use Micro\Framework\Kernel\Plugin\PluginCollectionInterface;
use Micro\Framework\BootDependency\Plugin\DependencyProviderInterface;
use Micro\Plugin\ConfigurationHelper\Business\Path\PathResolverFactory;
use Micro\Plugin\ConfigurationHelper\Business\Path\PathResolverFactoryInterface;
use Micro\Plugin\ConfigurationHelper\Business\Plugin\PluginClassResolverFactory;
use Micro\Plugin\ConfigurationHelper\Business\Plugin\PluginClassResolverFactoryInterface;
use Micro\Plugin\ConfigurationHelper\Business\Plugin\PluginClassResolverInterface;
use Micro\Plugin\ConfigurationHelper\Facade\ConfigurationHelperFacade;
use Micro\Plugin\ConfigurationHelper\Facade\ConfigurationHelperFacadeInterface;

class ConfigurationHelperPlugin implements DependencyProviderInterface
{
    public function provideDependencies(MutableContainerInterface $container): void
    {
        $container->register(ConfigurationHelperFacadeInterface::class, function (PluginCollectionInterface $pluginCollection) {
            return $this->createFacade($pluginCollection);
        });
    }

    protected function createFacade(PluginCollectionInterface $pluginCollection): ConfigurationHelperFacadeInterface
    {
        $classResolverFactory = $this->createPluginClassResolverFactory($pluginCollection);
        $classResolver = $classResolverFactory->create();
        $pathResolver = $this->createPathResolverFactoryInterface($classResolver)->create();

        return new ConfigurationHelperFacade($pathResolver);
    }

    protected function createPluginClassResolverFactory(PluginCollectionInterface $pluginCollection): PluginClassResolverFactoryInterface
    {
        return new PluginClassResolverFactory($pluginCollection);
    }

    protected function createPathResolverFactoryInterface(PluginClassResolverInterface $pluginClassResolver): PathResolverFactoryInterface
    {
        return new PathResolverFactory($pluginClassResolver);
    }
}
