<?php

/*
 *  This file is part of the Micro framework package.
 *
 *  (c) Stanislau Komar <kost@micro-php.net>
 *
 *  For the full copyright and license information, please view the LICENSE
 *  file that was distributed with this source code.
 */

namespace Micro\Framework\Kernel;

use Micro\Framework\Kernel\Plugin\PluginBootLoaderInterface;
use Micro\Framework\Kernel\Plugin\PluginRegistry;
use Psr\Container\ContainerExceptionInterface;
use Psr\Container\ContainerInterface;
use Psr\Container\NotFoundExceptionInterface;

class Kernel implements KernelInterface
{
    private bool $isStarted;

    private readonly PluginRegistry $pluginRegistry;

    /**
     * @param class-string[]              $pluginCollection
     * @param PluginBootLoaderInterface[] $pluginBootLoaderCollection
     */
    public function __construct(
        private readonly array $pluginCollection,
        private array $pluginBootLoaderCollection,
        private readonly ContainerInterface $container,
        ?PluginRegistry $pluginRegistry = null
    ) {
        $this->isStarted = false;
        $this->pluginRegistry = $pluginRegistry ?? new PluginRegistry();
    }

    public function addBootLoader(PluginBootLoaderInterface $bootLoader): self
    {
        if ($this->isStarted) {
            throw new \LogicException('Bootloaders must be installed before starting the kernel.');
        }

        $this->pluginBootLoaderCollection[] = $bootLoader;

        return $this;
    }

    public function setBootLoaders(iterable $bootLoaders): self
    {
        $this->pluginBootLoaderCollection = [];

        foreach ($bootLoaders as $loader) {
            $this->addBootLoader($loader);
        }

        return $this;
    }

    /**
     * {@inheritDoc}
     */
    public function run(): void
    {
        if ($this->isStarted) {
            return;
        }

        $this->loadPlugins();
        $this->isStarted = true;
    }

    /**
     * {@inheritDoc}
     */
    public function container(): ContainerInterface
    {
        return $this->container;
    }

    /**
     * {@inheritDoc}
     */
    public function loadPlugin(string $pluginClass): void
    {
        if ($this->pluginRegistry->has($pluginClass)) {
            return;
        }

        try {
            $plugin = $this->container->get($pluginClass);
            foreach ($this->pluginBootLoaderCollection as $bootLoader) {
                $bootLoader->boot($plugin);
            }

            $this->pluginRegistry->add($pluginClass, $plugin);
        } catch (NotFoundExceptionInterface|ContainerExceptionInterface $e) {
            // Silently skip for now
        }
    }

    /**
     * {@inheritDoc}
     */
    public function plugins(?string $pluginInterface = null): \Traversable
    {
        yield from $this->pluginRegistry->plugins($pluginInterface);
    }

    protected function loadPlugins(): void
    {
        foreach ($this->pluginCollection as $pluginClass) {
            $this->loadPlugin($pluginClass);
        }
    }
}
