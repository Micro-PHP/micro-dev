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

namespace Micro\Plugin\Cache\Business\Adapter;

use Micro\Plugin\Cache\Configuration\Adapter\CachePoolConfigurationInterface;
use Psr\Cache\CacheException;
use Psr\Cache\CacheItemPoolInterface;

interface ConcreteAdapterFactoryInterface
{
    /**
     * @throws CacheException
     */
    public function create(CachePoolConfigurationInterface $configuration): CacheItemPoolInterface;

    public function type(): string;
}
