<?php

namespace Micro\Plugin\Temporal\Workflow\Client\Repository;

interface ClientRepositoryFactoryInterface
{
    /**
     * @return ClientRepositoryInterface
     */
    public function create(): ClientRepositoryInterface;
}