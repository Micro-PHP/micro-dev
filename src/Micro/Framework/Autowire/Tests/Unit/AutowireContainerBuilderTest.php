<?php

declare(strict_types=1);

namespace Micro\Framework\Autowire\Tests\Unit;

use Micro\Framework\Autowire\Builder\AutowireContainerBuilder;
use Micro\Framework\Autowire\Definition\AutowiredClassDefinition;
use Micro\Framework\DependencyInjection\Definition\ServiceDefinition;
use PHPUnit\Framework\TestCase;

class AutowireContainerBuilderTest extends TestCase
{
    public function testBuildsAutowiredClassService(): void
    {
        $dependency = new AutowiredBuilderDependency();
        $container = (new AutowireContainerBuilder())
            ->service(new ServiceDefinition(
                AutowiredBuilderDependency::class,
                $dependency
            ))
            ->autowiredClass(new AutowiredClassDefinition(
                AutowiredBuilderService::class,
                AutowiredBuilderService::class
            ))
            ->build();

        $service = $container->get(AutowiredBuilderService::class);

        self::assertInstanceOf(AutowiredBuilderService::class, $service);
        self::assertSame($dependency, $service->dependency);
    }
}

class AutowiredBuilderDependency
{
}

readonly class AutowiredBuilderService
{
    public function __construct(public AutowiredBuilderDependency $dependency)
    {
    }
}
