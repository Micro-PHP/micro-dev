<?php

namespace Micro\Plugin\Temporal\Worker\Factory;

use Micro\Plugin\Temporal\Configuration\TemporalPluginConfigurationInterface;
use Micro\Plugin\Temporal\RoadRunner\Expander\Environment\EnvironmentExpanderFactoryInterface;
use Micro\Plugin\Temporal\Worker\Expander\WorkerExpanderFactoryInterface;
use Micro\Plugin\Temporal\Workflow\DataConverter\DataConverterFactoryInterface;
use Temporal\Worker\Transport\Goridge;
use Temporal\Worker\WorkerFactoryInterface as TemporalWorkerFactoryInterface;
use Temporal\Worker\WorkerOptions;

class WorkerFactory implements WorkerFactoryInterface
{
    /**
     * @param WorkerExpanderFactoryInterface $workerExpanderFactory
     * @param DataConverterFactoryInterface $dataConverterFactory
     * @param EnvironmentExpanderFactoryInterface $environmentExpanderFactory
     * @param TemporalPluginConfigurationInterface $pluginConfiguration
     */
    public function __construct(
        private readonly WorkerExpanderFactoryInterface $workerExpanderFactory,
        private readonly DataConverterFactoryInterface $dataConverterFactory,
        private readonly EnvironmentExpanderFactoryInterface $environmentExpanderFactory,
        private readonly TemporalPluginConfigurationInterface $pluginConfiguration
    )
    {
    }

    /**
     * {@inheritDoc}
     */
    public function create(string $workerName): TemporalWorkerFactoryInterface
    {
        $configuration = $this->pluginConfiguration->getWorkerConfig($workerName);
        $workerFactory = \Temporal\WorkerFactory::create(
            $this->dataConverterFactory->create(),
            Goridge::create($configuration)
        );

        $worker = $workerFactory->newWorker(
            $configuration->getQueueName(),
            WorkerOptions::new(),
        );

        $this->workerExpanderFactory->create()->expand($worker);
        $this->environmentExpanderFactory->create()->expand();

        return $workerFactory;
    }
}