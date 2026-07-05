<?php

namespace Micro\Plugin\Temporal\Worker\Expander;

use Micro\Framework\Autowire\AutowireHelperFactoryInterface;
use Micro\Plugin\Locator\Facade\LocatorFacadeInterface;

readonly class WorkerExpanderFactory implements WorkerExpanderFactoryInterface
{
    /**
     * @param LocatorFacadeInterface $locatorFacade
     * @param AutowireHelperFactoryInterface $autowireHelperFactory
     */
    public function __construct(
        private LocatorFacadeInterface           $locatorFacade,
        protected AutowireHelperFactoryInterface $autowireHelperFactory
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