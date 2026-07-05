<?php

declare(strict_types=1);

/*
 *  This file is part of the Micro framework package.
 *
 *  (c) Stanislau Komar <kost@micro-php.net>
 *
 *  For the full copyright and license information, please view the LICENSE
 *  file that was distributed with this source code.
 */

namespace Micro\Plugin\DTO\Business\FileLocator;

use Micro\Framework\Kernel\Plugin\PluginCollectionInterface;
use Micro\Plugin\DTO\DTOPluginConfigurationInterface;

readonly class FileLocatorFactory implements FileLocatorFactoryInterface
{
    public function __construct(
        private PluginCollectionInterface $pluginCollection,
        private DTOPluginConfigurationInterface $DTOPluginConfiguration
    ) {
    }

    /**
     * @return FileLocatorInterface
     */
    public function create(): FileLocatorInterface
    {
        return new FileLocator(
            DTOPluginConfiguration: $this->DTOPluginConfiguration,
            pluginCollection: $this->pluginCollection
        );
    }
}
