<?php

namespace Micro\Plugin\Temporal\Worker\Expander;

use Temporal\Worker\WorkerInterface;

interface WorkerExpanderInterface
{
    /**
     * @param WorkerInterface $worker
     * @return void
     */
    public function expand(WorkerInterface $worker): void;
}