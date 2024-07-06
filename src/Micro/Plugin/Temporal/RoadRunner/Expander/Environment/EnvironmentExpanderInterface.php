<?php

namespace Micro\Plugin\Temporal\RoadRunner\Expander\Environment;

interface EnvironmentExpanderInterface
{
    /**
     * @return mixed
     */
    public function expand();
}