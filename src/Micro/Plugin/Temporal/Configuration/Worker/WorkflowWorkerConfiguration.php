<?php

namespace Micro\Plugin\Temporal\Configuration\Worker;

use JetBrains\PhpStorm\ExpectedValues;
use Micro\Framework\BootConfiguration\Configuration\PluginRoutingKeyConfiguration;
use Spiral\RoadRunner\Environment\Mode;
use Temporal\Worker\WorkerFactoryInterface as TemporalWorkerFactoryInterface;

class WorkflowWorkerConfiguration extends PluginRoutingKeyConfiguration implements WorkflowWorkerConfigurationInterface
{

    const CFG_MODE = 'TEMPORAL_WORKER_%s_MODE';
    const CFG_RELAY_ADDRESS = 'TEMPORAL_WORKER_%s_RELAY_ADDRESS';
    const CFG_RPC_ADDRESS = 'TEMPORAL_WORKER_%s_RPC_ADDRESS';
    const CFG_QUEUE = 'TEMPORAL_WORKER_%s_QUEUE';

    /**
     * {@inheritDoc}
     */
    /**
     * {@inheritDoc}
     */
    public function getRelayAddress(): string
    {
        return $this->get(self::CFG_RELAY_ADDRESS, 'tcp://localhost:7233');
    }

    /**
     * {@inheritDoc}
     */
    public function getRPCAddress(): string
    {
        return $this->get(self::CFG_RPC_ADDRESS, 'tcp://localhost:6001');
    }

    /**
     * {@inheritDoc}
     */
    public function getQueueName(): string
    {
        return $this->get(self::CFG_QUEUE, TemporalWorkerFactoryInterface::DEFAULT_TASK_QUEUE);
    }

    #[ExpectedValues(valuesFromClass: Mode::class)] public function getMode(): string
    {
        return $this->get(self::CFG_MODE, 'tcp');
    }
}