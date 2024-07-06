<?php

namespace Micro\Plugin\Temporal\Worker\Expander;

interface WorkerExpanderFactoryInterface
{
    /**
     * @return WorkerExpanderInterface
     */
    public function create(): WorkerExpanderInterface;
}