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

namespace Micro\Plugin\Locator\Tests\Unit;

use Micro\Framework\KernelApp\AppKernel;
use Micro\Framework\Kernel\Plugin\PluginCollectionInterface;
use Micro\Plugin\EventEmitter\Business\Locator\EventListenerClassLocatorInterface;
use Micro\Plugin\EventEmitter\EventEmitterPlugin;
use Micro\Plugin\Locator\Facade\LocatorFacadeInterface;
use Micro\Plugin\Locator\Locator\Locator;
use PHPUnit\Framework\TestCase;

class LocatorPluginTest extends TestCase
{
    public function testPlugin()
    {
        $kernel = new AppKernel(
            [],
            [
                \stdClass::class,
            ],
            'dev'
        );

        $kernel->run();
        /** @var LocatorFacadeInterface $locator */
        $locator = $kernel->container()->get(LocatorFacadeInterface::class);
        $i = 0;
        foreach ($locator->lookup(EventListenerClassLocatorInterface::class) as $internalClass) {
            ++$i;
            $this->assertTrue(\in_array(EventListenerClassLocatorInterface::class, class_implements($internalClass)));
        }

        foreach ($locator->lookup('ClassNoExists') as $plugin) {
            throw new \Exception('Oh, no.');
        }

        $this->assertTrue((bool) $i);
    }

    public function testPluginClassDiscoveryExcludesTestsDirectories(): void
    {
        $locator = new class($this->createMock(PluginCollectionInterface::class)) extends Locator {
            /**
             * @return list<class-string>
             */
            public function pluginClasses(object $plugin): array
            {
                return iterator_to_array(
                    $this->getPluginClasses(new \ReflectionClass($plugin)),
                    false
                );
            }
        };

        $classes = $locator->pluginClasses(new EventEmitterPlugin());

        self::assertNotEmpty($classes);
        foreach ($classes as $class) {
            self::assertStringNotContainsString('\\Tests\\', $class);
        }
    }
}
