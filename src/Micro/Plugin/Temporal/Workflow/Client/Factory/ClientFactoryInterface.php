<?php

namespace Micro\Plugin\Temporal\Workflow\Client\Factory;

use Micro\Plugin\Temporal\Configuration\Client\WorkflowClientConfigurationInterface;
use Temporal\Client\WorkflowClientInterface;

interface ClientFactoryInterface
{
    /**
     * @param WorkflowClientConfigurationInterface $clientConfiguration
     *
     * @return WorkflowClientInterface
     */
    public function create(WorkflowClientConfigurationInterface $clientConfiguration): WorkflowClientInterface;
}