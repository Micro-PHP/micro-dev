<?php

namespace Micro\Plugin\Temporal\Worker\Factory;

use Temporal\Worker\WorkerFactoryInterface as TemporalWorkerFactoryInterface;

interface WorkerFactoryInterface
{
    /**
     * @param string $workerName
     * @return TemporalWorkerFactoryInterface
     */
    public function create(string $workerName): TemporalWorkerFactoryInterface;
}