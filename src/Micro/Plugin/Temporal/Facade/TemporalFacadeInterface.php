<?php

namespace Micro\Plugin\Temporal\Facade;

use Micro\Plugin\Temporal\Configuration\TemporalPluginConfigurationInterface;
use Temporal\Client\WorkflowClientInterface;
use Temporal\Internal\Support\Options;
use Temporal\Internal\Workflow\ActivityProxy;
use Temporal\Worker\WorkerFactoryInterface as TemporalWorkerFactoryInterface;

interface TemporalFacadeInterface
{
    /**
     * @param string $clientName
     *
     * @return WorkflowClientInterface
     */
    public function workflowClient(string $clientName = TemporalPluginConfigurationInterface::CLIENT_DEFAULT): WorkflowClientInterface;

    /**
     * @template T
     *
     * @param class-string<T> $activityInterface
     *
     * @return T
     */
    public function createActivityStub(string $activityInterface): ActivityProxy;

    /**
     * @return Options
     */
    public function createOptions(): Options;

    /**
     * @param string $workerName
     *
     * @return TemporalWorkerFactoryInterface
     */
    public function createWorker(string $workerName = 'default'): TemporalWorkerFactoryInterface;
}