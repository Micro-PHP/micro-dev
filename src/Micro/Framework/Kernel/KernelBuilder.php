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

use Micro\Framework\DependencyInjection\Builder\ContainerBuilder;
use Micro\Framework\Kernel\Plugin\PluginBootLoaderInterface;
use Micro\Framework\Kernel\Plugin\PluginRegistry;
use Psr\Container\ContainerInterface;

class KernelBuilder
{
    /**
     * @var class-string[]
     */
    private array $pluginCollection;

    /**
     * @var PluginBootLoaderInterface[]
     */
    private array $bootLoaderPluginCollection;

    private ?ContainerInterface $container;

    private ?PluginRegistry $pluginRegistry;

    public function __construct()
    {
        $this->pluginCollection = [];
        $this->bootLoaderPluginCollection = [];
        $this->container = null;
        $this->pluginRegistry = null;
    }

    /**
     * @param class-string[] $applicationPluginCollection
     *
     * @return $this
     */
    public function setApplicationPlugins(array $applicationPluginCollection): self
    {
        $this->pluginCollection = $applicationPluginCollection;

        return $this;
    }

    /**
     * @return $this
     */
    public function addBootLoader(PluginBootLoaderInterface $bootLoader): self
    {
        $this->bootLoaderPluginCollection[] = $bootLoader;

        return $this;
    }

    /**
     * @param PluginBootLoaderInterface[] $bootLoaderCollection
     *
     * @return $this
     */
    public function addBootLoaders(iterable $bootLoaderCollection): self
    {
        foreach ($bootLoaderCollection as $bootLoader) {
            $this->addBootLoader($bootLoader);
        }

        return $this;
    }

    /**
     * @param ContainerInterface $container
     *
     * @return $this
     */
    public function setContainer(ContainerInterface $container): self
    {
        $this->container = $container;

        return $this;
    }

    public function setPluginRegistry(PluginRegistry $pluginRegistry): self
    {
        $this->pluginRegistry = $pluginRegistry;

        return $this;
    }

    protected function container(): ContainerInterface
    {
        return $this->container ?? (new ContainerBuilder())->build();
    }

    /**
     * @return Kernel
     */
    public function build(): KernelInterface
    {
        return new Kernel(
            $this->pluginCollection,
            $this->bootLoaderPluginCollection,
            $this->container(),
            $this->pluginRegistry,
        );
    }
}
