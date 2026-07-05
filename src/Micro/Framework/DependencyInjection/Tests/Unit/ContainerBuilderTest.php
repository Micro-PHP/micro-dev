<?php

declare(strict_types=1);

namespace Micro\Framework\DependencyInjection\Tests\Unit;

use Micro\Framework\DependencyInjection\Builder\ContainerBuilder;
use Micro\Framework\DependencyInjection\Definition\DecoratorDefinition;
use Micro\Framework\DependencyInjection\Definition\FactoryDefinition;
use Micro\Framework\DependencyInjection\Definition\ServiceDefinition;
use PHPUnit\Framework\TestCase;

class ContainerBuilderTest extends TestCase
{
    public function testBuildsContainerFromInitializedServiceAndFactory(): void
    {
        $initializedService = new \stdClass();
        $factoryCalls = 0;

        $container = (new ContainerBuilder())
            ->service(new ServiceDefinition('initialized', $initializedService))
            ->factory(new FactoryDefinition('lazy', static function () use (&$factoryCalls): object {
                ++$factoryCalls;

                return new \stdClass();
            }))
            ->build();

        self::assertSame($initializedService, $container->get('initialized'));
        self::assertSame(0, $factoryCalls);

        $lazyService = $container->get('lazy');

        self::assertSame(1, $factoryCalls);
        self::assertSame($lazyService, $container->get('lazy'));
        self::assertSame(1, $factoryCalls);
    }

    public function testBuildsDecoratedFactory(): void
    {
        $container = (new ContainerBuilder())
            ->factory(new FactoryDefinition(
                NamedInterface::class,
                static fn (): NamedInterface => new NamedService('A')
            ))
            ->decorator(new DecoratorDefinition(
                NamedInterface::class,
                static fn (NamedInterface $service): NamedInterface =>
                    new NamedServiceDecorator($service, 'B')
            ))
            ->build();

        self::assertSame('AB', $container->get(NamedInterface::class)->getName());
    }

    public function testBuildsDecoratedValue(): void
    {
        $container = (new ContainerBuilder())
            ->service(new ServiceDefinition(
                NamedInterface::class,
                new NamedService('A')
            ))
            ->decorator(new DecoratorDefinition(
                NamedInterface::class,
                static fn (NamedInterface $service): NamedInterface =>
                    new NamedServiceDecorator($service, 'B')
            ))
            ->build();

        self::assertSame('AB', $container->get(NamedInterface::class)->getName());
        self::assertSame('AB', $container->get(NamedInterface::class)->getName());
    }
}
