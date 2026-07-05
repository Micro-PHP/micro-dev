<?php

/*
 *  This file is part of the Micro framework package.
 *
 *  (c) Stanislau Komar <kost@micro-php.net>
 *
 *  For the full copyright and license information, please view the LICENSE
 *  file that was distributed with this source code.
 */

namespace Micro\Framework\BootDependency\Boot;

use Micro\Framework\Autowire\AutowireHelperFactory;
use Micro\Framework\Autowire\AutowireHelperInterface;
use Micro\Framework\Autowire\ContainerAutowire;
use Micro\Framework\DependencyInjection\MutableContainerInterface;
use Micro\Framework\BootDependency\Plugin\DependencyProviderInterface;
use Micro\Framework\Kernel\Plugin\PluginBootLoaderInterface;

readonly class DependencyProviderBootLoader implements PluginBootLoaderInterface
{
    private MutableContainerInterface $container;

    public function __construct(MutableContainerInterface $container)
    {
        if (!($container instanceof ContainerAutowire)) {
            $container = new ContainerAutowire($container);
        }

        $this->container = $container;

        $this->container->register(
            AutowireHelperInterface::class,
            fn () => (new AutowireHelperFactory($this->container))->create()
        );
    }

    /**
     * {@inheritDoc}
     */
    public function boot(object $plugin): void
    {
        if (!($plugin instanceof DependencyProviderInterface)) {
            return;
        }

        $plugin->provideDependencies($this->container);
    }
}
