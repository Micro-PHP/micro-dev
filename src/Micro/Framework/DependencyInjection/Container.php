<?php

/*
 *  This file is part of the Micro framework package.
 *
 *  (c) Stanislau Komar <kost@micro-php.net>
 *
 *  For the full copyright and license information, please view the LICENSE
 *  file that was distributed with this source code.
 */

namespace Micro\Framework\DependencyInjection;

use Micro\Framework\DependencyInjection\Exception\ServiceNotRegisteredException;
use Micro\Framework\DependencyInjection\Exception\ServiceDecorationException;
use Micro\Framework\DependencyInjection\Exception\ServiceRegistrationException;
use Psr\Container\ContainerExceptionInterface;
use Psr\Container\NotFoundExceptionInterface;

/**
 * @author Stanislau Komar <head.trackingsoft@gmail.com>
 */
class Container implements MutableContainerInterface
{
    /** @var array<string, object> */
    private array $services = [];

    /**
     * @var array<class-string, callable(Container): object>
     */
    private array $servicesRaw = [];

    /**
     * @var array<class-string, array<int, array<callable(object, Container): object>>>
     */
    private array $decorators = [];

    /** @param iterable<string, object> $services */
    public function __construct(iterable $services = [])
    {
        foreach ($services as $id => $service) {
            $this->set($id, $service);
        }
    }

    /**
     * @psalm-suppress MoreSpecificImplementedParamType
     * @psalm-suppress MixedPropertyTypeCoercion
     *
     * @template T of object
     *
     * @param class-string<T> $id
     *
     * @return object
     *
     * @throws ContainerExceptionInterface
     * @throws NotFoundExceptionInterface
     */
    public function get(string $id): object
    {
        if (\array_key_exists($id, $this->services)) {
            $this->applyDecorators($id);

            return $this->services[$id];
        }

        $this->initializeService($id);

        return $this->services[$id];
    }

    /**
     * @param class-string $id
     *
     * @psalm-suppress MoreSpecificImplementedParamType
     */
    public function has(string $id): bool
    {
        return \array_key_exists($id, $this->servicesRaw)
            || \array_key_exists($id, $this->services);
    }

    public function set(string $id, object $service): void
    {
        if ($this->has($id)) {
            throw new ServiceRegistrationException(sprintf('Service "%s" already registered', $id));
        }

        $this->services[$id] = $service;
    }

    /**
     * {@inheritDoc}
     */
    public function register(string $id, callable $service): void
    {
        if ($this->has($id)) {
            throw new ServiceRegistrationException(sprintf('Service "%s" already registered', $id));
        }

        $this->servicesRaw[$id] = $service;
    }

    /**
     * {@inheritDoc}
     *
     * @psalm-suppress InvalidPropertyAssignmentValue
     */
    public function decorate(string $id, callable $service, int $priority = 0): void
    {
        if (!\array_key_exists($id, $this->decorators)) {
            $this->decorators[$id] = [];
        }
        $this->decorators[$id][$priority][] = $service;
    }

    /**
     * @template T of Object
     *
     * @param class-string<T> $serviceId
     */
    protected function initializeService(string $serviceId): void
    {
        if (empty($this->servicesRaw[$serviceId])) {
            throw new ServiceNotRegisteredException($serviceId);
        }

        $raw = $this->servicesRaw[$serviceId];
        $service = $raw($this);
        $this->services[$serviceId] = $service;

        $this->applyDecorators($serviceId);
    }

    private function applyDecorators(string $serviceId): void
    {
        if (!\array_key_exists($serviceId, $this->decorators)) {
            return;
        }

        $decoratorsByPriority = $this->decorators[$serviceId];
        unset($this->decorators[$serviceId]);
        krsort($decoratorsByPriority);

        foreach ($decoratorsByPriority as $decorators) {
            foreach ($decorators as $decorator) {
                $decorated = $decorator(
                    $this->services[$serviceId],
                    $this
                );

                if (!\is_object($decorated)) {
                    throw new ServiceDecorationException($serviceId, $decorated);
                }

                $this->services[$serviceId] = $decorated;
            }
        }
    }
}
