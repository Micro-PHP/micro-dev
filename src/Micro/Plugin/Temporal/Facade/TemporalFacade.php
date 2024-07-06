<?php

namespace Micro\Plugin\Temporal\Facade;

use Micro\Plugin\Temporal\Activity\Factory\ActivityStubFactoryInterface;
use Micro\Plugin\Temporal\Configuration\TemporalPluginConfigurationInterface;
use Micro\Plugin\Temporal\Worker\Factory\WorkerFactoryInterface;
use Micro\Plugin\Temporal\Workflow\Client\Repository\ClientRepositoryInterface;
use Temporal\Client\WorkflowClientInterface;
use Temporal\Client\WorkflowOptions;
use Temporal\Internal\Support\Options;
use Temporal\Internal\Workflow\ActivityProxy;
use Temporal\Worker\WorkerFactoryInterface as TemporalWorkerFactoryInterface;

class TemporalFacade implements TemporalFacadeInterface
{
    /**
     * @param ClientRepositoryInterface $clientRepository
     * @param WorkerFactoryInterface $workerFactory
     * @param ActivityStubFactoryInterface $activityStubFactory
     */
    public function __construct(
        private readonly ClientRepositoryInterface $clientRepository,
        private readonly WorkerFactoryInterface $workerFactory,
        private readonly ActivityStubFactoryInterface $activityStubFactory
    )
    {
    }

    /**
     * {@inheritDoc}
     */
    public function workflowClient(string $clientName = TemporalPluginConfigurationInterface::CLIENT_DEFAULT): WorkflowClientInterface
    {
        return $this->clientRepository->client($clientName);
    }

    /**
     * {@inheritDoc}
     */
    public function createActivityStub(string $activityInterface): ActivityProxy
    {
        return $this->activityStubFactory->create($activityInterface);
    }

    /**
     * {@inheritDoc}
     */
    public function createWorker(string $workerName = 'default'): TemporalWorkerFactoryInterface
    {
        return $this->workerFactory->create($workerName);
    }

    /**
     * {@inheritDoc}
     */
    public function createOptions(): Options
    {
        return WorkflowOptions::new();
    }
}