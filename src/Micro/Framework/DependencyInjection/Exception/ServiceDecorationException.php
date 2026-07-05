<?php

declare(strict_types=1);

namespace Micro\Framework\DependencyInjection\Exception;

use Psr\Container\ContainerExceptionInterface;

class ServiceDecorationException extends \RuntimeException implements ContainerExceptionInterface
{
    public function __construct(string $serviceId, mixed $decorated)
    {
        parent::__construct(sprintf(
            'Decorator for service "%s" must return an object, %s returned.',
            $serviceId,
            get_debug_type($decorated)
        ));
    }
}
