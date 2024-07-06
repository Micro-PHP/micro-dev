<?php

namespace Micro\Plugin\Temporal\Worker\Expander;

use Micro\Component\DependencyInjection\Autowire\AutowireHelperFactoryInterface;
use Micro\Plugin\Locator\Facade\LocatorFacadeInterface;

class WorkerExpanderFactory implements WorkerExpanderFactoryInterface
{
    /**
     * @param LocatorFacadeInterface $locatorFacade
     * @param AutowireHelperFactoryInterface $autowireHelperFactory
     */
    public function __construct(
        private readonly LocatorFacadeInterface $locatorFacade,
        protected readonly AutowireHelperFactoryInterface $autowireHelperFactory
    )
    {
    }

    /**
     * {@inheritDoc}
     */
    public function create(): WorkerExpanderInterface
    {
        return new WorkerExpander(
            $this->locatorFacade,
            $this->autowireHelperFactory
        );
    }
}