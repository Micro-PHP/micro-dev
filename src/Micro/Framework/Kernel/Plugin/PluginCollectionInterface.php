<?php

declare(strict_types=1);

namespace Micro\Framework\Kernel\Plugin;

interface PluginCollectionInterface
{
    /**
     * @template T of object
     *
     * @param class-string<T>|null $pluginInterface
     *
     * @return \Traversable<T|object>
     */
    public function plugins(?string $pluginInterface = null): \Traversable;
}
