<?php

namespace Micro\Plugin\Temporal\Configuration\Client;

interface WorkflowClientConfigurationInterface
{
    /**
     * @return string
     */
    public function getTemporalHost(): string;

    /**
     * @return int
     */
    public function getTemporalPort(): int;
}