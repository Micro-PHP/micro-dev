<?php

/*
 *  This file is part of the Micro framework package.
 *
 *  (c) Stanislau Komar <kost@micro-php.net>
 *
 *  For the full copyright and license information, please view the LICENSE
 *  file that was distributed with this source code.
 */

namespace Micro\Framework\DependencyInjection\Tests\Unit;

use Micro\Framework\DependencyInjection\Container;
use Micro\Framework\DependencyInjection\Exception\ServiceDecorationException;
use Micro\Framework\DependencyInjection\Exception\ServiceNotRegisteredException;
use Micro\Framework\DependencyInjection\Exception\ServiceRegistrationException;
use PHPUnit\Framework\TestCase;

class ContainerTest extends TestCase
{
    public function testContainerResolveDependencies(): void
    {
        $container = new Container();

        $container->register('test', function () {
            return new NamedService('success');
        });

        /** @var NamedInterface $service */
        $service = $container->get('test');
        $this->assertIsObject($service);
        $this->assertInstanceOf(NamedInterface::class, $service);
        $this->assertInstanceOf(NamedService::class, $service);
        $this->assertEquals('success', $service->getName());
    }

    public function testRegisterTwoServicesWithEqualAliasesException(): void
    {
        $this->expectException(ServiceRegistrationException::class);
        $container = new Container();

        $container->register('test', function () { return new class() {}; });
        $container->register('test', function () { return new class() {}; });
    }

    public function testContainerUnresolvedException(): void
    {
        $this->expectException(ServiceNotRegisteredException::class);

        $container = new Container();
        $container->register(NamedInterface::class, function (): NamedInterface {
            return new NamedService('success');
        });

        $container->get('test2');
    }

    public function testDecorateService(): void
    {
        $container = new Container();

        $container->register(NamedInterface::class, function (): NamedInterface {
            return new NamedService('A');
        });

        $container->decorate(NamedInterface::class, function (NamedInterface $decorated) {
            return new NamedServiceDecorator($decorated, 'D');
        });

        $container->decorate(NamedInterface::class, function (NamedInterface $decorated) {
            return new NamedServiceDecorator($decorated, 'B');
        }, 10);

        $container->decorate(NamedInterface::class, function (NamedInterface $decorated) {
            return new NamedServiceDecorator($decorated, 'C');
        }, 5);

        $result = $container->get(NamedInterface::class);

        $this->assertInstanceOf(NamedServiceDecorator::class, $result);
        $this->assertInstanceOf(NamedInterface::class, $result);
        $this->assertEquals('ABCD', $result->getName());

        $container->get(NamedInterface::class);
    }

    public function testUnregisteredException(): void
    {
        $container = new Container();
        $service = 'UnresolvedService';

        $this->expectException(ServiceNotRegisteredException::class);

        try {
            $container->get($service);
        } catch (ServiceNotRegisteredException $exception) {
            $this->assertEquals($service, $exception->getServiceId());

            throw $exception;
        }
    }

    public function testDecoratorsWithSamePriority(): void
    {
        $container = new Container();

        $container->register(NamedInterface::class, function (): NamedInterface {
            return new NamedService('A');
        });

        $container->decorate(NamedInterface::class, function (NamedInterface $decorated): NamedInterface {
            return new NamedServiceDecorator($decorated, 'B');
        }, 10);

        $container->decorate(NamedInterface::class, function (NamedInterface $decorated): NamedInterface {
            return new NamedServiceDecorator($decorated, 'D');
        });

        $container->decorate(NamedInterface::class, function (NamedInterface $decorated): NamedInterface {
            return new NamedServiceDecorator($decorated, 'E');
        });

        $container->decorate(NamedInterface::class, function (NamedInterface $decorated): NamedInterface {
            return new NamedServiceDecorator($decorated, 'C');
        }, 10);

        $result = $container->get(NamedInterface::class);
        $this->assertInstanceOf(NamedServiceDecorator::class, $result);
        $this->assertInstanceOf(NamedInterface::class, $result);
        $this->assertEquals('ABCDE', $result->getName());
    }

    public function testDecoratorMustReturnObject(): void
    {
        $service = new NamedService('A');
        $container = new Container([NamedInterface::class => $service]);
        $container->decorate(
            NamedInterface::class,
            static fn (): string => 'invalid'
        );

        try {
            $container->get(NamedInterface::class);
            self::fail('Expected decorator validation to fail.');
        } catch (ServiceDecorationException $exception) {
            self::assertSame(
                'Decorator for service "'.NamedInterface::class.'" must return an object, string returned.',
                $exception->getMessage()
            );
        }

        self::assertSame($service, $container->get(NamedInterface::class));
    }
}
