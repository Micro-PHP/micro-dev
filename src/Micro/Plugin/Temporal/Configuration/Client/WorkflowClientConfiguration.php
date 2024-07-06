<?php

namespace Micro\Plugin\Temporal\Configuration\Client;

use Micro\Framework\BootConfiguration\Configuration\PluginRoutingKeyConfiguration;

class
WorkflowClientConfiguration extends PluginRoutingKeyConfiguration implements WorkflowClientConfigurationInterface
{
    const CFG_TEMPORAL_HOST = 'TEMPORAL_CLIENT_%s_HOST';
    const CFG_TEMPORAL_PORT = 'TEMPORAL_CLIENT_%s_PORT';

    /**
     * {@inheritDoc}
     */
    public function getTemporalHost(): string
    {
        return $this->get(self::CFG_TEMPORAL_HOST, 'localhost');
    }

    /**
     * {@inheritDoc}
     */
    public function getTemporalPort(): int
    {
        return (int) $this->get(self::CFG_TEMPORAL_PORT, 7233);
    }
}