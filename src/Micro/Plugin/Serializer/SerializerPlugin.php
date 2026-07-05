<?php

namespace Micro\Plugin\Serializer;

use Micro\Framework\DependencyInjection\MutableContainerInterface;
use Micro\Framework\Kernel\Plugin\PluginCollectionInterface;
use Micro\Framework\BootDependency\Plugin\DependencyProviderInterface;
use Micro\Plugin\Serializer\Business\Pool\SerializerPool;
use Micro\Plugin\Serializer\Business\Serializer\SerializerInterface;
use Micro\Plugin\Serializer\Facade\SerializerFacade;
use Micro\Plugin\Serializer\Facade\SerializerFacadeInterface;

class SerializerPlugin implements DependencyProviderInterface
{
    public function provideDependencies(MutableContainerInterface $container): void
    {
        $container->register(SerializerFacadeInterface::class, function (
            PluginCollectionInterface $pluginCollection
        ) {
            return $this->createSerializerFacade($pluginCollection);
        });
    }

    protected function createSerializerFacade(PluginCollectionInterface $pluginCollection): SerializerFacadeInterface
    {
        return new SerializerFacade(
            $this->createSerializerPool($pluginCollection)
        );
    }

    protected function createSerializerPool(PluginCollectionInterface $pluginCollection): SerializerInterface
    {
        return new SerializerPool($pluginCollection);
    }
}
