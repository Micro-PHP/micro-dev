<?php

namespace Micro\Plugin\Temporal\Configuration\RoadRunner;

use JetBrains\PhpStorm\ExpectedValues;
use Micro\Framework\BootConfiguration\Configuration\PluginRoutingKeyConfiguration;
use Spiral\RoadRunner\Environment\Mode;

class RoadRunnerConfiguration extends PluginRoutingKeyConfiguration implements RoadRunnerConfigurationInterface
{
    const CFG_MODE = 'TEMPORAL_RR_MODE';
    const CFG_RELAY_ADDRESS = 'TEMPORAL_RR_RELAY_ADDRESS';
    const CFG_RPC_ADDRESS = 'TEMPORAL_RR_RPC_ADDRESS';

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

    #[ExpectedValues(valuesFromClass: Mode::class)]
    public function getMode(): string
    {
        return $this->get(self::CFG_MODE, 'tcp');
    }
}