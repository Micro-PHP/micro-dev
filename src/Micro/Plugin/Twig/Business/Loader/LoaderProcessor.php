<?php

/*
 *  This file is part of the Micro framework package.
 *
 *  (c) Stanislau Komar <kost@micro-php.net>
 *
 *  For the full copyright and license information, please view the LICENSE
 *  file that was distributed with this source code.
 */

namespace Micro\Plugin\Twig\Business\Loader;

use Micro\Framework\Kernel\Plugin\PluginCollectionInterface;
use Twig\Environment;
use Twig\Error\Error;
use Twig\Error\LoaderError;

readonly class LoaderProcessor implements LoaderProcessorInterface
{
    /**
     * @param LoaderInterface[] $loaders
     */
    public function __construct(
        private PluginCollectionInterface $pluginCollection,
        private iterable $loaders
    ) {
    }

    /**
     * {@inheritDoc}
     */
    public function load(Environment $environment): void
    {
        foreach ($this->pluginCollection->plugins() as $plugin) {
            $this->process($environment, $plugin);
        }
    }

    /**
     * @throws Error
     * @throws LoaderError
     */
    protected function process(Environment $environment, object $plugin): void
    {
        foreach ($this->loaders as $loader) {
            $loader->load($environment, $plugin);
        }
    }
}
