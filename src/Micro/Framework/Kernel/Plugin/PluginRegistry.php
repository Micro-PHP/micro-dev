<?php

declare(strict_types=1);

namespace Micro\Framework\Kernel\Plugin;

class PluginRegistry implements PluginCollectionInterface
{
    /** @var array<class-string, object> */
    private array $plugins = [];

    public function has(string $pluginClass): bool
    {
        return \array_key_exists($pluginClass, $this->plugins);
    }

    public function add(string $pluginClass, object $plugin): void
    {
        $this->plugins[$pluginClass] = $plugin;
    }

    public function plugins(?string $pluginInterface = null): \Traversable
    {
        foreach ($this->plugins as $plugin) {
            if ($pluginInterface === null || $plugin instanceof $pluginInterface) {
                yield $plugin;
            }
        }
    }
}
