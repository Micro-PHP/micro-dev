<?php

/*
 *  This file is part of the Micro framework package.
 *
 *  (c) Stanislau Komar <kost@micro-php.net>
 *
 *  For the full copyright and license information, please view the LICENSE
 *  file that was distributed with this source code.
 */

namespace Micro\Plugin\Twig;

use Micro\Framework\DependencyInjection\MutableContainerInterface;
use Micro\Framework\Kernel\Plugin\PluginCollectionInterface;
use Micro\Framework\BootConfiguration\Plugin\ConfigurableInterface;
use Micro\Framework\BootDependency\Plugin\DependencyProviderInterface;
use Micro\Framework\BootConfiguration\Plugin\PluginConfigurationTrait;
use Micro\Plugin\Twig\Business\Environment\EnvironmentFactory;
use Micro\Plugin\Twig\Business\Environment\EnvironmentFactoryInterface;
use Micro\Plugin\Twig\Business\Loader\ExtensionLoader;
use Micro\Plugin\Twig\Business\Loader\LoaderInterface;
use Micro\Plugin\Twig\Business\Loader\LoaderProcessor;
use Micro\Plugin\Twig\Business\Loader\LoaderProcessorInterface;
use Micro\Plugin\Twig\Business\Loader\TemplateLoader;
use Micro\Plugin\Twig\Business\Render\TwigRendererFactory;
use Micro\Plugin\Twig\Business\Render\TwigRendererFactoryInterface;

/**
 * @method TwigPluginConfigurationInterface configuration()
 */
class TwigPlugin implements DependencyProviderInterface, ConfigurableInterface
{
    use PluginConfigurationTrait;

    private PluginCollectionInterface $pluginCollection;

    public function provideDependencies(MutableContainerInterface $container): void
    {
        $container->register(TwigFacadeInterface::class, function (
            PluginCollectionInterface $pluginCollection
        ) {
            $this->pluginCollection = $pluginCollection;

            return $this->createTwigFacade();
        });
    }

    protected function createTwigFacade(): TwigFacadeInterface
    {
        return new TwigFacade(
            $this->createTwigRendererFactory()
        );
    }

    protected function createTwigRendererFactory(): TwigRendererFactoryInterface
    {
        return new TwigRendererFactory(
            $this->createEnvironmentFactory()
        );
    }

    protected function createEnvironmentFactory(): EnvironmentFactoryInterface
    {
        return new EnvironmentFactory(
            $this->configuration(),
            $this->createLoaderProcessor()
        );
    }

    protected function createLoaderProcessor(): LoaderProcessorInterface
    {
        return new LoaderProcessor($this->pluginCollection, $this->createLoaders());
    }

    /**
     * @return LoaderInterface[]
     */
    protected function createLoaders(): array
    {
        return [
            new ExtensionLoader(),
            new TemplateLoader(),
        ];
    }
}
