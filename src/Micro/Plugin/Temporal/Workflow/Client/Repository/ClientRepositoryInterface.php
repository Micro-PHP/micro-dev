<?php

namespace Micro\Plugin\Temporal\Workflow\Client\Repository;

use Temporal\Client\WorkflowClientInterface;

interface ClientRepositoryInterface
{
    /**
     * @param string $clientName
     * @return WorkflowClientInterface
     */
    public function client(string $clientName): WorkflowClientInterface;
}