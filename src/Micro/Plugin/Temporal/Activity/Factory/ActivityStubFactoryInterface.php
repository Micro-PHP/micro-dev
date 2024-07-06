<?php

namespace Micro\Plugin\Temporal\Activity\Factory;

use Temporal\Internal\Workflow\ActivityProxy;

interface ActivityStubFactoryInterface
{
    /**
     * @template T
     *
     * @param class-string<T> $activityInterface
     *
     * @return T
     */
    public function create(string $activityInterface): ActivityProxy;
}