<?php

namespace Micro\Plugin\Temporal\Activity\Factory;

use Temporal\Activity\ActivityOptions;
use Temporal\Internal\Workflow\ActivityProxy;
use Temporal\Workflow;

class ActivityStubFactory implements ActivityStubFactoryInterface
{
    /**
     * {@inheritDoc}
     */
    public function create(string $activityInterface): ActivityProxy
    {
        return Workflow::newActivityStub($activityInterface,
            ActivityOptions::new()
        );
    }
}