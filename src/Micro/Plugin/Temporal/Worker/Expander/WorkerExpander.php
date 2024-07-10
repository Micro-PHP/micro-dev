<?php

namespace Micro\Plugin\Temporal\Worker\Expander;

use Micro\Component\DependencyInjection\Autowire\AutowireHelperFactoryInterface;
use Micro\Plugin\Locator\Facade\LocatorFacadeInterface;
use Micro\Plugin\Temporal\Activity\ActivityInterface;
use Micro\Plugin\Temporal\Workflow\WorkflowInterface;
use Temporal\Worker\WorkerInterface;

class WorkerExpander implements WorkerExpanderInterface
{
    /**
     * @param LocatorFacadeInterface $locatorFacade
     * @param AutowireHelperFactoryInterface $autowireHelperFactory
     */
    public function __construct(
        readonly LocatorFacadeInterface $locatorFacade,
        private readonly AutowireHelperFactoryInterface $autowireHelperFactory
    )
    {
    }

    /**
     * {@inheritDoc}
     */
    public function expand(WorkerInterface $worker): void
    {
        foreach ($this->locatorFacade->lookup(ActivityInterface::class) as $activityClass) {
            $worker->registerActivity(
                $activityClass,
                $this->autowireHelperFactory
                    ->create()
                    ->autowire($activityClass)
            );
        }

        foreach ($this->locatorFacade->lookup(WorkflowInterface::class) as $workflowClass) {
            $worker->registerWorkflowTypes($workflowClass);
        }
    }
}