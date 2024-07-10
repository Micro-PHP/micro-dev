<?php

/*
 *  This file is part of the Micro framework package.
 *
 *  (c) Stanislau Komar <kost@micro-php.net>
 *
 *  For the full copyright and license information, please view the LICENSE
 *  file that was distributed with this source code.
 */

namespace Micro\Plugin\Logger\Facade;

use Micro\Plugin\Logger\Business\Provider\LoggerProviderInterface;
use Psr\Log\LoggerInterface;

readonly class LoggerFacade implements LoggerFacadeInterface
{
    public function __construct(private LoggerProviderInterface $loggerProvider)
    {
    }

    public function getLogger(?string $loggerName = null): LoggerInterface
    {
        if (null === $loggerName) {
            $loggerName = self::LOGGER_DEFAULT;
        }

        return $this->loggerProvider->getLogger($loggerName);
    }
}